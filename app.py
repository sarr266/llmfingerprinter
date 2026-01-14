import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

from config.settings import settings
from core.collector import collector
from core.analyzer import analyzer
from core.database import db

# Page config
st.set_page_config(
    page_title="LLM Fingerprinter - CTI Edition",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.big-title {
    font-size: 3rem;
    font-weight: bold;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.threat-high { background: #ef4444; color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold; }
.threat-medium { background: #f59e0b; color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold; }
.threat-low { background: #10b981; color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold; }
.bot-badge { background: #ef4444; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
.human-badge { background: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 10px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

def init_system():
    """Initialize the system"""
    if not st.session_state.initialized:
        with st.spinner("Initializing CTI system..."):
            try:
                settings.validate()
                success = collector.initialize()
                if success:
                    st.session_state.initialized = True
                    st.success("✅ System initialized!")
                else:
                    st.error("❌ Failed to login. Check cookies.json")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def main():
    # Header
    st.markdown('<h1 class="big-title">🎯 LLM Fingerprinter</h1>', unsafe_allow_html=True)
    st.markdown("**Cyber Threat Intelligence Edition - Bot Detection & Campaign Attribution**")
    
    # Initialize
    init_system()
    
    # Sidebar
    with st.sidebar:
        st.image("https://api.dicebear.com/7.x/bottts/svg?seed=cti", width=150)
        st.markdown("### 🔍 CTI Navigation")
        
        page = st.radio(
            "Select Module",
            ["📊 Threat Dashboard", "🔍 Collect Intel", "🧪 Analyze Threats", 
             "🎯 Campaigns", "🤖 Bot Profiles", "📄 CTI Report", "⚙️ Settings"]
        )
        
        st.markdown("---")
        st.markdown("### 📈 Quick Stats")
        stats = db.get_stats()
        st.metric("Tweets", stats['total_tweets'])
        st.metric("Threats", stats['bot_profiles'])
        st.metric("Analyzed", stats['analyzed_tweets'])
    
    # Route to pages
    if page == "📊 Threat Dashboard":
        show_dashboard()
    elif page == "🔍 Collect Intel":
        show_collect()
    elif page == "🧪 Analyze Threats":
        show_analyze()
    elif page == "🎯 Campaigns":
        show_campaigns()
    elif page == "🤖 Bot Profiles":
        show_bots()
    elif page == "📄 CTI Report":
        show_cti_report()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Threat Intelligence Dashboard")
    
    stats = db.get_stats()
    
    # Top metrics with enhanced styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{stats['total_tweets']}</h3>
            <p>Tweets Collected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{stats['analyzed_tweets']}</h3>
            <p>Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{stats['bot_profiles']}</h3>
            <p>Threats Detected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        campaigns = analyzer.get_campaigns()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(campaigns)}</h3>
            <p>Active Campaigns</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 Threat Classification")
        llm_dist = db.get_llm_distribution()
        
        if llm_dist:
            df = pd.DataFrame([
                {'Type': llm, 'Count': count}
                for llm, count in llm_dist.items()
            ])
            
            colors = {
                'generic-bot': '#ef4444',
                'gpt-4': '#3b82f6',
                'gpt-3.5': '#06b6d4',
                'claude': '#8b5cf6',
                'llama': '#f59e0b',
                'gemini': '#ec4899',
                'human': '#10b981'
            }
            
            fig = px.pie(df, values='Count', names='Type', hole=0.4,
                        color='Type', color_discrete_map=colors)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 No data yet. Collect and analyze tweets first!")
    
    with col2:
        st.subheader("🎯 Campaign Overview")
        
        campaigns = analyzer.get_campaigns()
        if campaigns:
            # Show threat levels
            threat_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for c in campaigns:
                level = c.get('threat_level', 'unknown')
                if level in threat_counts:
                    threat_counts[level] += 1
            
            fig = go.Figure(data=[
                go.Bar(name='HIGH', x=['Campaigns'], y=[threat_counts['HIGH']], marker_color='#ef4444'),
                go.Bar(name='MEDIUM', x=['Campaigns'], y=[threat_counts['MEDIUM']], marker_color='#f59e0b'),
                go.Bar(name='LOW', x=['Campaigns'], y=[threat_counts['LOW']], marker_color='#10b981')
            ])
            fig.update_layout(barmode='stack', height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎯 No campaigns detected yet")
    
    # Recent Activity
    st.markdown("---")
    st.subheader("🔥 Recent Threat Activity")
    
    if db.tweets:
        recent = sorted(db.tweets, key=lambda x: x.get('collected_at', ''), reverse=True)[:5]
        
        for tweet in recent:
            with st.expander(f"@{tweet.get('author_username', 'unknown')} - {tweet.get('keyword')}"):
                st.write(f"**Text:** {tweet.get('text', '')[:300]}...")
                
                if tweet.get('analyzed'):
                    fp = next((f for f in db.fingerprints if f.get('tweet_id') == tweet.get('id')), None)
                    if fp:
                        llm = fp.get('detected_llm')
                        conf = fp.get('confidence', 0)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Detected", llm.upper())
                        col2.metric("Confidence", f"{conf:.0%}")
                        
                        if llm != "human":
                            col3.markdown('<span class="bot-badge">THREAT</span>', unsafe_allow_html=True)
    else:
        st.info("📭 No data yet. Start collecting intelligence!")

def show_collect():
    st.header("🔍 Intelligence Collection")
    
    if not st.session_state.initialized:
        st.warning("⚠️ System not initialized. Check cookies.json file.")
        return
    
    # Show configured keywords
    st.info(f"🎯 Monitoring {len(settings.TRIGGER_KEYWORDS)} threat indicators")
    with st.expander("View Keywords"):
        st.write(", ".join(settings.TRIGGER_KEYWORDS))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Targeted Collection")
        
        keyword = st.selectbox("Select threat keyword", settings.TRIGGER_KEYWORDS)
        
        if st.button("🔍 Collect Intel", type="primary"):
            with st.spinner(f"Collecting intelligence on '{keyword}'..."):
                try:
                    result = collector.collect_keyword(keyword)
                    st.success(f"✅ Found {result['found']} tweets, saved {result['saved']}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("Bulk Operations")
        
        if st.button("🚀 Full Sweep", type="secondary"):
            with st.spinner("Running full intelligence sweep..."):
                progress = st.progress(0)
                try:
                    result = collector.collect_all_keywords()
                    progress.progress(100)
                    st.success(f"✅ Collected {result['total_tweets']} tweets!")
                    
                    # Show breakdown
                    for r in result['results']:
                        if 'error' not in r:
                            st.write(f"• {r['keyword']}: {r['saved']} tweets")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if st.button("👥 Enrich Profiles"):
            with st.spinner("Enriching threat actor profiles..."):
                count = collector.enrich_profiles(20)
                st.success(f"✅ Enriched {count} profiles")
    
    st.markdown("---")
    st.subheader("📋 Collection Log")
    
    if db.tweets:
        df_data = []
        for t in sorted(db.tweets, key=lambda x: x.get('collected_at', ''), reverse=True)[:30]:
            df_data.append({
                'Time': t.get('collected_at', '')[:19],
                'Author': f"@{t.get('author_username')}",
                'Keyword': t.get('keyword'),
                'Preview': t.get('text', '')[:80] + '...',
                'Status': '✅ Analyzed' if t.get('analyzed') else '⏳ Pending'
            })
        
        st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
    else:
        st.info("📭 No intelligence collected yet. Click 'Full Sweep' to start!")

def show_analyze():
    st.header("🧪 Threat Analysis Engine")
    
    unanalyzed = db.get_unanalyzed_tweets()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"📊 {len(unanalyzed)} tweets awaiting analysis")
        
        limit = st.slider("Batch size", 10, 200, 100)
        
        if st.button("🔬 Run Analysis", type="primary", disabled=len(unanalyzed) == 0):
            with st.spinner(f"Analyzing {limit} threats..."):
                progress = st.progress(0)
                
                try:
                    result = analyzer.batch_analyze(limit)
                    progress.progress(100)
                    
                    st.success(f"✅ Analyzed {result['analyzed']} tweets")
                    st.warning(f"🤖 Detected {result['bots_detected']} threats")
                    
                    if result['llm_breakdown']:
                        st.write("**Threat Breakdown:**")
                        for llm, count in result['llm_breakdown'].items():
                            st.write(f"• {llm}: {count}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("Analysis Settings")
        st.write(f"**Confidence Threshold:** {settings.MIN_CONFIDENCE_THRESHOLD:.0%}")
        st.write(f"**LLM Signatures:** {len(settings.KNOWN_LLM_FINGERPRINTS)}")
        st.write(f"**Detection Models:** 8")

def show_campaigns():
    st.header("🎯 Campaign Attribution")
    
    campaigns = analyzer.get_campaigns()
    
    if not campaigns:
        st.info("🎯 No campaigns detected yet. Analyze more tweets to identify patterns.")
        return
    
    st.write(f"**{len(campaigns)} active campaigns detected**")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    high = len([c for c in campaigns if c.get('threat_level') == 'HIGH'])
    medium = len([c for c in campaigns if c.get('threat_level') == 'MEDIUM'])
    low = len([c for c in campaigns if c.get('threat_level') == 'LOW'])
    
    col1.metric("🔴 High Threat", high)
    col2.metric("🟡 Medium Threat", medium)
    col3.metric("🟢 Low Threat", low)
    
    st.markdown("---")
    
    # Campaign cards
    for campaign in campaigns:
        threat_level = campaign.get('threat_level', 'unknown')
        
        if threat_level == 'HIGH':
            st.markdown('<div class="threat-high">⚠️ HIGH THREAT CAMPAIGN</div>', unsafe_allow_html=True)
        elif threat_level == 'MEDIUM':
            st.markdown('<div class="threat-medium">⚠️ MEDIUM THREAT CAMPAIGN</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="threat-low">ℹ️ LOW THREAT CAMPAIGN</div>', unsafe_allow_html=True)
        
        with st.expander(f"{campaign['llm'].upper()} Campaign - {campaign['bot_count']} bots"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Campaign Details:**")
                st.write(f"• Type: {campaign['bot_type']}")
                st.write(f"• Bots: {campaign['bot_count']}")
                st.write(f"• Total Tweets: {campaign['total_tweets']}")
                st.write(f"• Avg Confidence: {campaign['avg_confidence']:.0%}")
            
            with col2:
                st.write("**Target Keywords:**")
                for kw in campaign['keywords']:
                    st.write(f"• {kw}")
            
            st.write("**Sample Tweets:**")
            for sample in campaign['sample_tweets'][:3]:
                st.text(f"• {sample[:100]}...")
            
            st.write("**IOCs (Indicators of Compromise):**")
            st.code(", ".join(campaign['iocs']['usernames'][:10]))

def show_bots():
    st.header("🤖 Threat Actor Profiles")
    
    bots = [p for p in db.profiles.values() if p.get('is_bot', False)]
    
    if not bots:
        st.info("🤖 No bots detected yet. Run analysis first!")
        return
    
    st.write(f"**{len(bots)} threat actors identified**")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        bot_type_filter = st.selectbox("Filter by type", ["All"] + list(set(b.get('bot_type', 'unknown') for b in bots)))
    with col2:
        sort_by = st.selectbox("Sort by", ["Confidence", "Username", "Bot Type"])
    
    # Apply filters
    filtered_bots = bots
    if bot_type_filter != "All":
        filtered_bots = [b for b in bots if b.get('bot_type') == bot_type_filter]
    
    # Sort
    if sort_by == "Confidence":
        filtered_bots.sort(key=lambda x: x.get('bot_confidence', 0), reverse=True)
    elif sort_by == "Username":
        filtered_bots.sort(key=lambda x: x.get('username', ''))
    
    st.markdown("---")
    
    # Display bots
    for profile in filtered_bots[:50]:
        with st.expander(f"@{profile.get('username')} - {profile.get('bot_confidence', 0):.0%} confidence"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Profile:**")
                st.write(f"• Name: {profile.get('name')}")
                st.write(f"• Username: @{profile.get('username')}")
                st.write(f"• ID: {profile.get('user_id')}")
            
            with col2:
                st.write("**Metrics:**")
                st.write(f"• Followers: {profile.get('followers', 0):,}")
                st.write(f"• Following: {profile.get('following', 0):,}")
                st.write(f"• Tweets: {profile.get('tweet_count', 0):,}")
            
            with col3:
                st.write("**Threat Intel:**")
                st.write(f"• Type: {profile.get('bot_type', 'unknown')}")
                st.write(f"• LLM: {profile.get('detected_llm', 'unknown')}")
                st.write(f"• Confidence: {profile.get('bot_confidence', 0):.0%}")
            
            if profile.get('description'):
                st.write(f"**Bio:** {profile.get('description')}")

def show_cti_report():
    st.header("📄 CTI Intelligence Report")
    
    if st.button("📊 Generate Report", type="primary"):
        with st.spinner("Generating comprehensive CTI report..."):
            report = analyzer.generate_cti_report()
            
            st.success("✅ Report generated!")
            
            # Executive Summary
            st.subheader("📋 Executive Summary")
            summary = report['summary']
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Campaigns", summary['total_campaigns'])
            col2.metric("Threats Detected", summary['total_bots_detected'])
            col3.metric("Tweets Analyzed", summary['total_tweets_analyzed'])
            
            # Threat Breakdown
            st.subheader("🎯 Threat Breakdown")
            if summary['threat_breakdown']:
                df = pd.DataFrame([
                    {'Threat Type': k, 'Count': v}
                    for k, v in summary['threat_breakdown'].items()
                ])
                fig = px.bar(df, x='Threat Type', y='Count', color='Count')
                st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.subheader("💡 Recommendations")
            for rec in report['recommendations']:
                st.write(rec)
            
            # IOCs
            st.subheader("🔍 Indicators of Compromise (IOCs)")
            st.write(f"**Total IOCs:** {report['iocs']['total_indicators']}")
            
            with st.expander("View All Malicious Accounts"):
                for acc in report['iocs']['malicious_accounts'][:50]:
                    st.write(f"• @{acc['username']} (ID: {acc['user_id']}) - {acc['type']} - {acc['confidence']:.0%}")
            
            # Download options
            st.subheader("💾 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📥 Download Full Report (JSON)",
                    data=json.dumps(report, indent=2),
                    file_name=f"cti_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Create IOC list
                ioc_list = "\n".join([f"{acc['user_id']},@{acc['username']},{acc['type']},{acc['confidence']:.2f}" 
                                     for acc in report['iocs']['malicious_accounts']])
                
                st.download_button(
                    "📥 Download IOC List (CSV)",
                    data=f"user_id,username,threat_type,confidence\n{ioc_list}",
                    file_name=f"iocs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

def show_settings():
    st.header("⚙️ System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configuration")
        st.write(f"**Keywords Monitored:** {len(settings.TRIGGER_KEYWORDS)}")
        st.write(f"**Confidence Threshold:** {settings.MIN_CONFIDENCE_THRESHOLD:.0%}")
        st.write(f"**Max Tweets/Keyword:** {settings.MAX_TWEETS_PER_KEYWORD}")
        
        with st.expander("View All Keywords"):
            st.code("\n".join(settings.TRIGGER_KEYWORDS))
    
    with col2:
        st.subheader("Statistics")
        stats = db.get_stats()
        for key, value in stats.items():
            st.metric(key.replace('_', ' ').title(), value)
    
    st.markdown("---")
    
    # CTI Context
    st.subheader("🔍 CTI Capabilities")
    cti_context = settings.get_cti_context()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Primary Threats Monitored:**")
        for threat in cti_context['primary_threats']:
            st.write(f"• {threat}")
    
    with col2:
        st.write("**Detection Capabilities:**")
        for cap in cti_context['detection_capabilities']:
            st.write(f"• {cap}")
    
    st.markdown("---")
    st.subheader("💾 Data Export")
    
    if st.button("📥 Export All Data"):
        export = {
            'tweets': db.tweets,
            'profiles': db.profiles,
            'fingerprints': db.fingerprints,
            'metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'total_records': len(db.tweets) + len(db.profiles) + len(db.fingerprints)
            }
        }
        
        st.download_button(
            "💾 Download Complete Dataset",
            data=json.dumps(export, indent=2),
            file_name=f"llm_fingerprinter_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()